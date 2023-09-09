.PHONY: default clean run

src/ast.py: generate/generate_ast.py
	python3 generate/generate_ast.py src/ast.py

default: src/ast.py
clean:
	rm -f src/ast.py
run: default
	python3 main.py
