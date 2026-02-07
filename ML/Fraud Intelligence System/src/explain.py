import shap
import matplotlib.pyplot as plt

def explain_model(model, X_background):
    """
    SHAP explainer for XGBoost using probability output.
    Compatible with XGBoost 2.x
    """
    explainer = shap.Explainer(
        model.predict_proba,   # ✅ callable
        X_background
    )

    shap_values = explainer(X_background)
    return explainer, shap_values


def global_explanation(shap_values):
    """
    Global feature importance
    """
    shap.plots.beeswarm(shap_values[..., 1], show=False)
    plt.tight_layout()
    plt.show()


def local_explanation(shap_values, index=0):
    """
    Local explanation for a single sample
    """
    shap.plots.waterfall(shap_values[index, ..., 1], show=False)
    plt.show()
