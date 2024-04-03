import importlib
import joblib
import json
import os
import logging
from logs.logging_config import configure_logging

class modules:
    def __init__(self, model_path, vectorizer_path=None, modulesjson_path=None) -> None:
        configure_logging()
        self.logger = logging.getLogger(__name__)

        self.module_map = {}
        try:
            self.module_json = json.load(open(modulesjson_path, "r"))
        except Exception:
            self.logger.error(f"Error loading modules json, please check the modules json path.")

        if vectorizer_path and model_path:
            self.logger.info("Naive bayes classifier enabled, loading models...")
            try:
                self.load_models(model_path, vectorizer_path)
                self.detectable_available = True
            except Exception:
                self.logger.error(f"Error loading models, please check the model and vectorizer paths. Detected modules will not be loaded.")
                self.detectable_available = False
        else:
            self.logger.info("Naive bayes classifier disabled, using LLM for module detection, detectable modules will be treated as non-detectable.")
        self.load_modules()

    def load_models(self, model_path, vectorizer_path):
        model_filename = model_path
        self.loaded_model = joblib.load(model_filename)

        vectorizer_filename = vectorizer_path
        self.vectorizer = joblib.load(vectorizer_filename)
    
    def predict_module(self, query):
        if self.detectable_available:
            query_vector = self.vectorizer.transform([query])
            predictions = self.loaded_model.predict(query_vector)
            predicted_probabilities = self.loaded_model.predict_proba(query_vector)
            if max(predicted_probabilities[0]) < 0.9:
                return None, max(predicted_probabilities[0])
            return predictions[0], max(predicted_probabilities[0])
        else:
            self.logger.warning("Unable to predict modules using classifier, vectorizer and model not loaded.")
            return None, 100.0

    def load_modules(self):
        self.undetectable_modules = []
        self.detectable_modules = []
        for module_info in self.module_json:
            module_name = module_info["name"]
            module_file = f"modules/{module_name}.py" 
            if os.path.isfile(module_file):
                try:
                    module = importlib.import_module(f"modules.{module_name}")
                    if module_info.get("detectable", True):
                        if self.detectable_available:
                            self.detectable_modules.append(module_name)
                        else:
                            self.logger.warning(f"Module '{module_name}' is detectable but the classifier is not available, module will classified as undetectable.")
                            self.undetectable_modules.append(module_name)
                    else:
                        self.undetectable_modules.append(module_name)
                    self.module_map[module_name] = module
                    
                except ModuleNotFoundError:
                    pass

    def use_module(self, module_name, args, **kwargs):
        module = self.module_map.get(module_name)
        if module:
            for module_info in self.module_json:
                if module_info["name"] == module_name:
                    func_name = module_info.get("function", "default_function_name")
                    func = getattr(module, func_name, None)
                    if func and callable(func):
                        if isinstance(args, dict):
                            return func(**args, **kwargs)
                        else:
                            return func(args, **kwargs)
                    else:
                        self.logger.warning(f"Function '{func_name}' not found in module '{module_name}'. Unable to call function.")
                        return f"Function '{func_name}' not found in module '{module_name}'. Unable to call function."
            self.logger.warning(f"Module information for '{module_name}' not found in module_json.")
            return f"Module information for '{module_name}' not found in module_json."
        else:
            self.logger.warning(f"Module '{module_name}' not found.")
            return f"Module '{module_name}' not found"

    def get_undetectable_modules(self):
        return self.undetectable_modules
    
    def get_detectable_modules(self):
        return self.detectable_modules
    
    def get_arguments(self, module_name):
        module = self.module_map.get(module_name)
        if module:
            for module_info in self.module_json:
                if module_info["name"] == module_name:
                    return module_info.get("args")
            self.logger.warning(f"Module information for '{module_name}' not found in module_json.")
            return f"Module information for '{module_name}' not found in module_json."
        else:
            self.logger.warning(f"Module '{module_name}' not found.")
            return f"Module '{module_name}' not found."

if __name__ == '__main__':
    print('This is a handler, it is not meant to be run directly.')
    pass
    

