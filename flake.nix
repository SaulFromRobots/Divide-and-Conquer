{
	inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

	outputs = { self, nixpkgs }: let
		pkgs = nixpkgs.legacyPackages.x86_64-linux;
	in {
		devShells.x86_64-linux.default = with pkgs; mkShell {
			nativeBuildInputs = [
				(python3.withPackages (py: with py; [ flask sqlalchemy ipython ]))
				dbeaver-bin
			];
		};
	};
}
