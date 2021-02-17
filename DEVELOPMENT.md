# Install Dependencies
In Debian:

sudo apt install libcairo2-dev

sudo apt install libgirepository1.0-dev

# Virtual Environment
pipenv --three

pipenv shell

pipenv install

# Build
`sh build.sh`

# Execute
After building enter to `buildir/buildir/testdir/bin` and execute `./pyopentracks`.

# Internacionalization (i10n)
Enter to `po/` directory and execute `update_potfiles.sh` to create a new language PO file or update the string to a language. Then edit the PO file and execute `compile_potfiles.sh` to generate mo file.
