{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";

    sexp-python.url = "github:lispparser/sexp-python";
    sexp-python.inputs.nixpkgs.follows = "nixpkgs";
    sexp-python.inputs.flake-utils.follows = "flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, sexp-python }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python311Packages;
     in {
        packages = rec {
          default = supertux-tool;

          supertux-tool = pythonPackages.buildPythonPackage rec {
            pname = "supertux-tool";
            version = "0.0.0";

            src = ./.;

            buildPhase = ''
            '';

            installPhase = ''
            '';

            buildInputs = [
            ];

            propagatedBuildInputs = [
              sexp-python.packages.${system}.default
            ];

            nativeBuildInputs = [
            ];
          };
        };
}
    );
}
