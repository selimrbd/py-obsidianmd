#!/opt/homebrew/bin/zsh
coverage run -m pytest
coverage report
coverage html
open htmlcov/index.html
