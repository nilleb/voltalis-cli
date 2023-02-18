python3 -m venv venv

shell=`basename "$SHELL"`

if [ $shell = "fish" ]; then
    . venv/bin/activate.fish
else
    . venv/bin/activate
fi

python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r dev-requirements.txt
