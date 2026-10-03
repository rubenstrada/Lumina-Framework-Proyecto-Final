"""Ejecuta el proyecto completo usando la configuración declarada."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from lumina_framework.cli import main

if __name__ == '__main__':
    raise SystemExit(main(['--mode','run',*sys.argv[1:]]))
