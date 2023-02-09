init-env:
	brew install pyenv pyenv-virtualenv
	eval "$(pyenv init-)"
	eval "$(pyenv virtualenv-init -)";  
	export PATH="$HOME/.pyenv/bin:$PATH"
	pyenv install 3.9
	pyenv virtualenv 3.9 cuya-courts

env:
	pyenv local cuya-courts

init-db:
	python scripts/init_db.py