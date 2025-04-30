if [ -z "$BUILD_DIR" ]; then
  BUILD_DIR=./build
fi

# ~ expansion
CANONICAL_BUILD_DIR=$(eval echo "$BUILD_DIR")

mkdir -p "$CANONICAL_BUILD_DIR"
cp -r src/* "$CANONICAL_BUILD_DIR"
cp requirements.txt "$CANONICAL_BUILD_DIR"

cd "$CANONICAL_BUILD_DIR"
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
rm requirements.txt

echo "$CANONICAL_BUILD_DIR"
cat > run.sh <<EOF
  . "$CANONICAL_BUILD_DIR"/venv/bin/activate
  python3  "$CANONICAL_BUILD_DIR"/main.py # bash subprocess inherits STDIN
  deactivate
EOF
chmod +x run.sh
