import sys
import unittest
from datetime import datetime
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    import pymongo  # noqa: F401
except ModuleNotFoundError:
    pymongo_stub = ModuleType("pymongo")
    pymongo_stub.MongoClient = MagicMock(return_value=MagicMock())
    pymongo_stub.ReturnDocument = SimpleNamespace(AFTER=True)
    sys.modules["pymongo"] = pymongo_stub

import pandas as pd


SAMPLE_HISTORICAL = pd.DataFrame({
    "entity_id": [1, 2, 3, 4],
    "entity_type": ["House", "Hospital", "SolarFarm", "Factory"],
    "district": ["District-A", "District-B", "District-C", "District-D"],
    "weather": ["Cloudy", "Sunny", "Rainy", "Windy"],
    "temperature": [20, 25, 18, 22],
    "timestamp": pd.to_datetime([
        "2026-06-01 08:00:00",
        "2026-06-01 09:00:00",
        "2026-06-01 18:00:00",
        "2026-06-02 10:00:00",
    ]),
    "peak_hour": ["Yes", "Yes", "Yes", "No"],
    "energy_consumed_kwh": [120.0, 900.0, 300.0, 1500.0],
    "energy_generated_kwh": [80.0, 200.0, 1200.0, 400.0],
    "grid_usage_kwh": [40.0, 700.0, 0.0, 1100.0],
    "energy_price": [0.2, 0.25, 0.18, 0.3],
    "carbon_emission_kg": [20.0, 300.0, 0.0, 500.0],
    "anomaly": [0, 0, 0, 1],
})


def _mock_model_assets():
    model = MagicMock()
    model.predict.return_value = [0]
    model.predict_proba.return_value = [[0.82, 0.18]]
    return {
        "model": model,
        "accuracy": 0.91,
        "features": [
            "entity_id",
            "temperature",
            "energy_consumed_kwh",
            "energy_generated_kwh",
            "grid_usage_kwh",
            "energy_price",
            "carbon_emission_kg",
            "entity_type_House",
            "district_District-A",
            "weather_Cloudy",
            "peak_hour_Yes",
        ],
        "training_date": "2026-06-01 12:00:00",
        "training_samples": 1000,
        "feature_count": 11,
    }


def _mock_context():
    return {
        "users": [
            {
                "username": "hospital",
                "role": "Hospital",
                "energy_consumed": 900,
                "energy_generated": 200,
                "energy_balance": 50,
            },
            {
                "username": "solar-farm",
                "role": "SolarFarm",
                "energy_consumed": 300,
                "energy_generated": 1200,
                "energy_balance": 400,
            },
        ],
        "historical": SAMPLE_HISTORICAL.copy(),
        "marketplace_summary": {
            "average_price": 15,
            "highest_price": 20,
            "lowest_price": 10,
            "market_volume": 5000,
        },
        "marketplace_transactions": [
            {"quantity": 50, "total_price": 750},
        ],
        "energy_transactions": [],
        "approved_records": [],
        "current_consumption": 1200.0,
        "current_generation": 1400.0,
        "grid_usage": 0.0,
        "average_marketplace_price": 15.0,
        "market_volume": 5000.0,
        "trade_volume": 750.0,
        "traded_energy": 50.0,
        "user_count": 2,
    }


class AIServiceTests(unittest.TestCase):

    @patch("app.services.ai_service._get_model_assets", return_value=_mock_model_assets())
    @patch("app.services.ai_service._collect_live_context", return_value=_mock_context())
    def test_compute_prediction_uses_model_and_live_data(
        self,
        collect_context,
        model_assets,
    ):
        from app.services.ai_service import compute_prediction

        result = compute_prediction()

        self.assertEqual(result["current_consumption"], 1200.0)
        self.assertIn("prediction", result)
        self.assertIn("prediction_difference", result)
        self.assertEqual(result["confidence"], 82.0)
        model_assets()["model"].predict.assert_called_once()

    @patch("app.services.ai_service._collect_live_context", return_value=_mock_context())
    def test_compute_forecast_returns_horizons_and_trend(
        self,
        collect_context,
    ):
        from app.services.ai_service import compute_forecast

        forecast = compute_forecast()

        self.assertIn("next_hour_prediction", forecast)
        self.assertIn("next_day_prediction", forecast)
        self.assertIn("next_week_prediction", forecast)
        self.assertIn(forecast["trend"], ["Increasing", "Decreasing", "Stable"])
        self.assertIsInstance(forecast["peak_hour"], int)
        self.assertIsInstance(forecast["lowest_demand_hour"], int)

    @patch("app.services.ai_service._predict_user_ml_signal")
    @patch("app.services.ai_service._get_model_assets", return_value=_mock_model_assets())
    @patch("app.services.ai_service._collect_live_context")
    def test_detect_anomalies_flags_high_usage(
        self,
        collect_context,
        model_assets,
        predict_signal,
    ):
        from app.services.ai_service import detect_anomalies

        context = _mock_context()
        context["users"] = [{
            "username": "factory",
            "role": "Factory",
            "energy_consumed": 2500,
            "energy_generated": 200,
            "energy_balance": 0,
        }]
        collect_context.return_value = context
        predict_signal.return_value = (
            "Critical",
            "Machine learning model flagged critical anomaly",
            90,
        )

        with patch("app.services.ai_service.compute_prediction") as compute_prediction:
            compute_prediction.return_value = {
                "current_consumption": 2500,
                "expected_consumption": 1100,
                "prediction": 2600,
                "prediction_difference": 100,
                "confidence": 88,
                "anomaly_signal": 1,
            }
            anomalies = detect_anomalies(context)

        self.assertTrue(anomalies)
        self.assertEqual(anomalies[0]["affected_user"], "factory")
        self.assertIn(anomalies[0]["status"], ["Warning", "Critical"])

    @patch("app.services.ai_service._get_model_assets", return_value=_mock_model_assets())
    @patch("app.services.ai_service._collect_live_context", return_value=_mock_context())
    def test_generate_recommendations_use_marketplace_data(
        self,
        collect_context,
        model_assets,
    ):
        from app.services.ai_service import (
            compute_forecast,
            compute_prediction,
            detect_anomalies,
            generate_smart_recommendations,
        )

        context = _mock_context()
        prediction = compute_prediction(context)
        forecast = compute_forecast(context)
        recommendations = generate_smart_recommendations(
            context,
            prediction,
            forecast,
            [],
        )

        self.assertTrue(recommendations)
        recommendation_types = {item["type"] for item in recommendations}
        self.assertTrue(
            recommendation_types.intersection({
                "sell_excess_energy",
                "high_marketplace_prices",
                "low_marketplace_prices",
                "maintain_operations",
            })
        )

    @patch("app.services.ai_service.os.path.getmtime", return_value=datetime(2026, 6, 1).timestamp())
    @patch("app.services.ai_service._load_historical_dataframe", return_value=SAMPLE_HISTORICAL.copy())
    @patch("app.services.ai_service.joblib.load")
    def test_get_model_information(
        self,
        joblib_load,
        load_hist,
        getmtime,
    ):
        from app.services.ai_service import get_model_information

        joblib_load.side_effect = [
            _mock_model_assets()["model"],
            0.91,
            _mock_model_assets()["features"],
        ]

        info = get_model_information()

        self.assertEqual(info["algorithm"], "RandomForestClassifier")
        self.assertEqual(info["accuracy"], 91.0)
        self.assertEqual(info["model_status"], "READY")
        self.assertEqual(info["feature_count"], 11)

    @patch("app.services.ai_service._get_analytics")
    @patch("app.services.ai_service.get_monitoring_data")
    @patch("app.services.ai_service.get_model_information")
    @patch("app.services.ai_service.count_ai_alerts", return_value=4)
    @patch("app.services.ai_service.detect_anomalies", return_value=[])
    @patch("app.services.ai_service.compute_forecast")
    @patch("app.services.ai_service.compute_prediction")
    @patch("app.services.ai_service._collect_live_context", return_value=_mock_context())
    @patch("app.services.ai_service._ml_engine")
    def test_get_ai_dashboard_returns_required_fields(
        self,
        ml_engine,
        collect_context,
        compute_prediction,
        compute_forecast,
        detect_anomalies,
        count_alerts,
        model_info,
        monitoring_data,
        analytics,
    ):
        from app.services.ai_service import get_ai_dashboard

        ml_engine.return_value = {
            "calculate_risk_score": lambda *args, **kwargs: 20,
            "get_risk_level": lambda score: "LOW",
            "generate_recommendation": lambda level: "Monitor trends",
        }

        compute_prediction.return_value = {
            "current_consumption": 1200,
            "expected_consumption": 1100,
            "prediction": 1250,
            "prediction_difference": 50,
            "confidence": 88,
            "anomaly_signal": 0,
        }
        compute_forecast.return_value = {
            "next_hour_prediction": 100,
            "next_day_prediction": 2400,
            "next_week_prediction": 16800,
            "trend": "Stable",
            "peak_hour": 18,
            "lowest_demand_hour": 4,
        }
        model_info.return_value = {
            "algorithm": "RandomForestClassifier",
            "accuracy": 91.0,
            "training_samples": 1000,
            "feature_count": 11,
            "last_training_time": "2026-06-01 12:00:00",
            "model_status": "READY",
            "model_version": "RandomForestClassifier-v1",
        }
        monitoring_data.return_value = {
            "anomaly_rate": 5,
            "risk_score": 20,
        }
        analytics.return_value = {
            "energy_efficiency": 85,
        }

        dashboard = get_ai_dashboard()

        self.assertEqual(dashboard["ai_accuracy"], 91.0)
        self.assertEqual(dashboard["prediction_confidence"], 88)
        self.assertEqual(dashboard["current_demand"], 1200)
        self.assertEqual(dashboard["predicted_demand"], 1250)
        self.assertEqual(dashboard["total_ai_alerts"], 4)
        self.assertIn("recommendation", dashboard)
        self.assertIn("system_status", dashboard)

    @patch("app.services.ai_service.get_model_information")
    @patch("app.services.ai_service.get_history_statistics")
    @patch("app.services.ai_service.count_predictions", return_value=12)
    @patch("app.services.ai_service.count_ai_alerts", return_value=5)
    @patch("app.services.ai_service.count_critical_alerts", return_value=1)
    @patch("app.services.ai_service.count_alerts_by_severity")
    def test_get_ai_statistics(
        self,
        count_by_severity,
        count_critical,
        count_alerts,
        count_predictions,
        history_stats,
        model_info,
    ):
        from app.services.ai_service import get_ai_statistics

        count_by_severity.side_effect = [1, 2, 1, 1]
        history_stats.return_value = {
            "average_confidence": 86.5,
            "average_accuracy": 86.5,
            "highest_risk": "HIGH",
            "lowest_risk": "LOW",
        }
        model_info.return_value = {"accuracy": 91.0}

        stats = get_ai_statistics()

        self.assertEqual(stats["total_predictions"], 12)
        self.assertEqual(stats["total_alerts"], 5)
        self.assertEqual(stats["critical_alerts"], 1)
        self.assertEqual(stats["average_confidence"], 86.5)
        self.assertEqual(stats["highest_risk"], "HIGH")

    @patch("app.services.ai_service.save_ai_history")
    @patch("app.services.ai_service.save_ai_alert")
    @patch("app.services.ai_service.generate_smart_recommendations")
    @patch("app.services.ai_service.detect_anomalies", return_value=[])
    @patch("app.services.ai_service.compute_forecast")
    @patch("app.services.ai_service.compute_prediction")
    @patch("app.services.ai_service._collect_live_context", return_value=_mock_context())
    @patch("app.services.ai_service._ml_engine")
    def test_run_full_analysis_stores_history_and_returns_results(
        self,
        ml_engine,
        collect_context,
        compute_prediction,
        compute_forecast,
        detect_anomalies,
        recommendations,
        save_alert,
        save_history,
    ):
        from app.services.ai_service import run_full_analysis

        ml_engine.return_value = {
            "calculate_risk_score": lambda *args, **kwargs: 15,
            "get_risk_level": lambda score: "LOW",
            "should_create_ai_alert": lambda level: False,
            "generate_recommendation": lambda level: "Stable",
        }

        compute_prediction.return_value = {
            "current_consumption": 1200,
            "expected_consumption": 1100,
            "prediction": 1250,
            "prediction_difference": 50,
            "confidence": 88,
            "anomaly_signal": 0,
        }
        compute_forecast.return_value = {
            "next_hour_prediction": 100,
            "next_day_prediction": 2400,
            "next_week_prediction": 16800,
            "trend": "Stable",
            "peak_hour": 18,
            "lowest_demand_hour": 4,
        }
        recommendations.return_value = [{
            "type": "maintain_operations",
            "message": "System metrics are stable.",
            "priority": "LOW",
        }]
        save_history.return_value = {
            "prediction": 1250,
            "confidence": 88,
            "risk_level": "LOW",
        }

        result = run_full_analysis()

        self.assertEqual(result["prediction"]["prediction"], 1250)
        self.assertEqual(result["alerts_created"], 0)
        save_history.assert_called_once()

    @patch("app.routes.ai_routes.get_ai_dashboard")
    def test_ai_dashboard_route(self, dashboard):
        from flask import Flask
        from app.routes.ai_routes import ai_bp

        dashboard.return_value = {
            "ai_accuracy": 91.0,
            "risk_level": "LOW",
        }
        app = Flask(__name__)
        app.register_blueprint(ai_bp)
        client = app.test_client()

        response = client.get("/api/ai/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["ai_accuracy"], 91.0)

    @patch("app.routes.ai_routes.run_full_analysis")
    def test_ai_run_route(self, run_analysis):
        from flask import Flask
        from app.routes.ai_routes import ai_bp

        run_analysis.return_value = {
            "prediction": {"prediction": 1000},
            "alerts_created": 1,
        }
        app = Flask(__name__)
        app.register_blueprint(ai_bp)
        client = app.test_client()

        response = client.post("/api/ai/run")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["alerts_created"], 1)

    @patch("app.routes.ai_routes.get_model_information")
    def test_ai_model_route(self, model_info):
        from flask import Flask
        from app.routes.ai_routes import ai_bp

        model_info.return_value = {
            "algorithm": "RandomForestClassifier",
            "accuracy": 91.0,
            "model_status": "READY",
        }
        app = Flask(__name__)
        app.register_blueprint(ai_bp)
        client = app.test_client()

        response = client.get("/api/ai/model")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["algorithm"], "RandomForestClassifier")

    @patch("database.mongodb.ai_history_repository.get_ai_history_collection")
    def test_ai_history_repository_persists_records(
        self,
        get_collection,
    ):
        from database.mongodb.ai_history_repository import (
            save_ai_history,
            get_ai_history,
        )

        collection = MagicMock()
        get_collection.return_value = collection

        record = save_ai_history({
            "prediction": 1200,
            "confidence": 90,
            "risk_level": "LOW",
            "recommendation": "Stable",
            "timestamp": "2026-06-29 10:00:00",
            "model_version": "RandomForestClassifier-v1",
        })

        self.assertEqual(record["prediction"], 1200)
        collection.insert_one.assert_called_once()

        collection.find.return_value.sort.return_value.limit.return_value = [
            record
        ]
        history = get_ai_history()

        self.assertEqual(len(history), 1)

    @patch("database.mongodb.ai_alert_repository.get_ai_alert_collection")
    def test_ai_alert_repository_normalizes_severity(
        self,
        get_collection,
    ):
        from database.mongodb.ai_alert_repository import save_ai_alert

        collection = MagicMock()
        get_collection.return_value = collection

        alert = save_ai_alert({
            "username": "hospital",
            "generated": 100,
            "consumed": 900,
            "reason": "High usage",
            "risk_level": "high",
            "timestamp": "2026-06-29 10:00:00",
        })

        self.assertEqual(alert["severity"], "HIGH")
        self.assertEqual(alert["risk_level"], "HIGH")


if __name__ == "__main__":
    unittest.main()
