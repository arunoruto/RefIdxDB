{
  pkgs,
  ...
}:

{
  # Python's urllib has no baked-in CA bundle on NixOS; point it at cacert so
  # `refidxdb db --download` (and the sync test) can verify TLS certificates.
  env = {
    SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";
  };

  # https://devenv.sh/scripts/
  scripts = {
    refidxdb.exec = ''uv run refidxdb "$@"'';
  };

  enterShell = ''
    if [ ! -L "$DEVENV_ROOT/.venv" ]; then
        ln -s "$DEVENV_STATE/venv/" "$DEVENV_ROOT/.venv"
    fi
  '';

  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
    uv run refidxdb --version
  '';
  languages.python = {
    enable = true;
    # version = "3.12";

    uv = {
      enable = true;
      sync = {
        enable = true;
        groups = [
          "test"
          # "docs"
        ];
      };
    };

    libraries = [ pkgs.zlib ];
  };
}
