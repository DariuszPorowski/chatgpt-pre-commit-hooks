#!/bin/bash

mkdir -p ../.vhs_demo_repo ../.vhs_demo_repo/demo ../.vhs_demo_repo/chatgpt_pre_commit_hooks
cp -r pyproject.toml ../.vhs_demo_repo
cp -r .gitignore ../.vhs_demo_repo
cp -r demo/* ../.vhs_demo_repo/demo/
cp -r demo/.[^.]* ../.vhs_demo_repo/demo/
cp -r chatgpt_pre_commit_hooks/* ../.vhs_demo_repo/chatgpt_pre_commit_hooks/
pushd ../.vhs_demo_repo || exit
git config --global init.defaultBranch main
git init
git config --local user.name github-actions[bot]
git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
git config --local commit.gpgsign false

if [ "${1}" != "ci" ]; then
	python -m venv .venv
	source .venv/bin/activate
else
	sudo apt-get install -y figlet lolcat ffmpeg
fi

# download_url=$(curl -sL https://api.github.com/repos/tsl0922/ttyd/releases/latest | jq -r '.assets | map(select(.name | contains("x86_64")))[] | .browser_download_url')
# curl -sSLo ttyd "${download_url}"
# chmod +x ttyd

# download_url=$(curl -sL https://api.github.com/repos/charmbracelet/vhs/releases/latest | jq -r '.assets | map(select(.name | contains("Linux_x86_64") and endswith(".tar.gz")))[] | .browser_download_url')
# curl -sSLo vhs.tar.gz "${download_url}"
# tar -xf vhs.tar.gz vhs
# rm -f vhs.tar.gz
# chmod +x vhs

# cargo install lolcrab
python -m pip install -U . .[dev]
python -m pip install pre-commit
pre-commit uninstall && pre-commit install --config demo/.pre-commit-config.yaml
git add .
git commit -m "Initial commit"
vhs demo/chatgpt_commit_message.tape
popd || exit
# rm -rf ../.vhs_demo_repo
