{ python }:
let
  inherit (builtins) getAttr fromTOML readFile;
  pyproject = fromTOML (readFile ./pyproject.toml);
  dependencies = pyproject.project.dependencies;
in
python.pkgs.buildPythonPackage {
  inherit (pyproject.project) name version;
  format = "pyproject";
  src = ./.;

  buildInputs = [ python.pkgs.setuptools ];
  propagatedBuildInputs = map (x: getAttr x python.pkgs) dependencies;
  doCheck = false;
}
