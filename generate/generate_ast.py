import argparse

parser = argparse.ArgumentParser(prog="generate_ast", description="generates the AST")
parser.add_argument("filename")
args = parser.parse_args()
filename = args.filename

expr_classes = [
    ("BinaryExpr",   (("Expr", "left"), ("Token", "operator"), ("Expr", "right")),),
    ("GroupingExpr", (("Expr", "expression"),),                                   ),
    ("LiteralExpr",  (("object", "value"),),                                      ),
    ("UnaryExpr",    (("Token", "operator"), ("Expr", "right")),                  ),
]

stmt_classes = [
    ("ExpressionStmt", (("Expr", "expression"),)),
    ("PrintStmt",      (("Expr", "expression"),)),
]

def camel_case(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")

result = ["# AUTOGENERATED"]
result.append("from dataclasses import dataclass")
result.append("from .tokenizer import Token")

def generate_dataclasses(basename, classes):
    # generate visitor interface
    result.append(    f"")
    result.append(    f"class {basename}VisitorInterface:")
    for classname, _ in classes:
        result.append(f"    def accept_{camel_case(classname)}(self, {basename.lower()}: '{classname}'):")
        result.append(f"        assert(0)  # must be implemented")

    # generate dataclasses
    result.append(f"")
    result.append(f"@dataclass")
    result.append(f"class {basename}:")
    result.append(f"    def accept(self, visitor: {basename}VisitorInterface):")
    result.append(f"        assert(0)  # not implemented for bare {basename}")

    for classname, members in classes:
        result.append(    f"")
        result.append(    f"@dataclass")
        result.append(    f"class {classname}({basename}):")
        for member in members:
            result.append(f"    {member[1]}: {member[0]}")
        result.append(    f"    def accept(self, visitor: {basename}VisitorInterface):")
        result.append(    f"        return visitor.accept_{camel_case(classname)}(self)")

generate_dataclasses("Expr", expr_classes)
generate_dataclasses("Stmt", stmt_classes)

with open(filename, "w") as file:
    file.write("\n".join(result))
