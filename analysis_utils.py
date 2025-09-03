from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Numeric
from sqlalchemy.orm import aliased

from models.sqlalchemy_models import NFHSStateData, NFHSDistrictData, State, District, Indicator


# ------------------------------
# Indicator Statistics Function
# ------------------------------
async def compute_indicator_stats(data, db: AsyncSession):
    stats_data = []

    column_mapping = {
        "ST": "st",
        "Non-ST": "non_st",
        "Total": "total"
    }

    category_value = data.category_type
    if category_value not in column_mapping:
        raise ValueError(f"Invalid category_type: {category_value}")

    column_name = column_mapping[category_value]

    # CASE 1: District-level (state is selected)
    if data.selected_state:
        selected_category = getattr(NFHSDistrictData, column_name)

        for indicator_id in data.selected_indicators:
            # Min
            min_stmt = (
                select(District.district_name, selected_category)
                .join(NFHSDistrictData, NFHSDistrictData.district_id == District.district_id)
                .where(
                    NFHSDistrictData.indicator_id == indicator_id,
                    District.state_id == data.selected_state
                )
                .order_by(selected_category.asc())
                .limit(1)
            )
            min_row = (await db.execute(min_stmt)).first()
            min_val = f"{min_row[1]} ({min_row[0]})" if min_row else None

            # Max
            max_stmt = (
                select(District.district_name, selected_category)
                .join(NFHSDistrictData, NFHSDistrictData.district_id == District.district_id)
                .where(
                    NFHSDistrictData.indicator_id == indicator_id,
                    District.state_id == data.selected_state
                )
                .order_by(selected_category.desc())
                .limit(1)
            )
            max_row = (await db.execute(max_stmt)).first()
            max_val = f"{max_row[1]} ({max_row[0]})" if max_row else None

            # Mean & Stddev
            stats_stmt = (
                select(
                    func.avg(cast(selected_category, Numeric)),
                    func.stddev(cast(selected_category, Numeric))
                )
                .join(District, District.district_id == NFHSDistrictData.district_id)
                .where(
                    NFHSDistrictData.indicator_id == indicator_id,
                    District.state_id == data.selected_state
                )
            )
            mean_val, stddev_val = (await db.execute(stats_stmt)).first()

            indicator = await db.get(Indicator, indicator_id)

            stats_data.append({
                "indicator_id": indicator_id,
                "indicator_name": indicator.indicator_name if indicator else None,
                "min_value": min_val,
                "max_value": max_val,
                "mean": float(mean_val) if mean_val else None,
                "standard deviation": float(stddev_val) if stddev_val else None,
                "level": "district"
            })

    # CASE 2: State-level (default)
    else:
        selected_category = getattr(NFHSStateData, column_name)

        for indicator_id in data.selected_indicators:
            # Min
            min_stmt = (
                select(State.state_name, selected_category)
                .join(NFHSStateData, NFHSStateData.state_id == State.state_id)
                .where(NFHSStateData.indicator_id == indicator_id)
                .order_by(selected_category.asc())
                .limit(1)
            )
            min_row = (await db.execute(min_stmt)).first()
            min_val = f"{min_row[1]} ({min_row[0]})" if min_row else None

            # Max
            max_stmt = (
                select(State.state_name, selected_category)
                .join(NFHSStateData, NFHSStateData.state_id == State.state_id)
                .where(NFHSStateData.indicator_id == indicator_id)
                .order_by(selected_category.desc())
                .limit(1)
            )
            max_row = (await db.execute(max_stmt)).first()
            max_val = f"{max_row[1]} ({max_row[0]})" if max_row else None

            # Mean & Stddev
            stats_stmt = (
                select(
                    func.avg(cast(selected_category, Numeric)),
                    func.stddev(cast(selected_category, Numeric))
                )
                .where(NFHSStateData.indicator_id == indicator_id)
            )
            mean_val, stddev_val = (await db.execute(stats_stmt)).first()

            indicator = await db.get(Indicator, indicator_id)

            stats_data.append({
                "indicator_id": indicator_id,
                "indicator_name": indicator.indicator_name if indicator else None,
                "min_value": min_val,
                "max_value": max_val,
                "mean": float(mean_val) if mean_val else None,
                "standard deviation": float(stddev_val) if stddev_val else None,
                "level": "state"
            })

    return stats_data


# ------------------------------
# Indicator Correlation Function
# ------------------------------
async def compute_indicator_correlations(data, db: AsyncSession):
    correlations = []
    indicator_ids = data.selected_indicators

    if not indicator_ids or len(indicator_ids) < 2:
        raise ValueError("At least 2 indicators required for correlation")

    # CASE 1: District-level
    if data.selected_state:
        for i, ind_x in enumerate(indicator_ids):
            for ind_y in indicator_ids[i+1:]:
                NFHSD1 = aliased(NFHSDistrictData)
                NFHSD2 = aliased(NFHSDistrictData)

                corr_stmt = (
                    select(
                        func.corr(
                            cast(NFHSD1.total, Numeric),
                            cast(NFHSD2.total, Numeric)
                        )
                    )
                    .join(NFHSD2, (NFHSD1.district_id == NFHSD2.district_id))
                    .join(District, District.district_id == NFHSD1.district_id)
                    .where(
                        NFHSD1.indicator_id == ind_x,
                        NFHSD2.indicator_id == ind_y,
                        District.state_id == data.selected_state
                    )
                )
                result = (await db.execute(corr_stmt)).scalar()

                ind_x_obj = await db.get(Indicator, ind_x)
                ind_y_obj = await db.get(Indicator, ind_y)

                correlations.append({
                    "indicator_x_id": ind_x,
                    "indicator_x_name": ind_x_obj.indicator_name if ind_x_obj else None,
                    "indicator_y_id": ind_y,
                    "indicator_y_name": ind_y_obj.indicator_name if ind_y_obj else None,
                    "correlation": float(result) if result is not None else None,
                    "level": "district"
                })

    # CASE 2: State-level
    else:
        for i, ind_x in enumerate(indicator_ids):
            for ind_y in indicator_ids[i+1:]:
                NFHS1 = aliased(NFHSStateData)
                NFHS2 = aliased(NFHSStateData)

                corr_stmt = (
                    select(
                        func.corr(
                            cast(NFHS1.total, Numeric),
                            cast(NFHS2.total, Numeric)
                        )
                    )
                    .join(NFHS2, (NFHS1.state_id == NFHS2.state_id))
                    .where(
                        NFHS1.indicator_id == ind_x,
                        NFHS2.indicator_id == ind_y
                    )
                )
                result = (await db.execute(corr_stmt)).scalar()

                ind_x_obj = await db.get(Indicator, ind_x)
                ind_y_obj = await db.get(Indicator, ind_y)

                correlations.append({
                    "indicator_x_id": ind_x,
                    "indicator_x_name": ind_x_obj.indicator_name if ind_x_obj else None,
                    "indicator_y_id": ind_y,
                    "indicator_y_name": ind_y_obj.indicator_name if ind_y_obj else None,
                    "correlation": float(result) if result is not None else None,
                    "level": "state"
                })

    return correlations
