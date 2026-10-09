"""Lance tous les tests sans pytest (alternative simple : `pytest`)."""
import importlib.util, pathlib
total = 0
for fichier in sorted(pathlib.Path("tests").glob("test_*.py")):
    spec = importlib.util.spec_from_file_location(fichier.stem, fichier)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    for nom in dir(module):
        if nom.startswith("test_"):
            getattr(module, nom)(); total += 1
print(f"{total} tests passés")
