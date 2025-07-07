.PHONY: preview
preview:
	cd website && quarto preview

.PHONY: setup-py
setup-py:
	uv venv venv
	source venv/bin/activate && uv pip install -r requirements.txt


.PHONY: setup-quarto
setup-quarto:
	cd website && \
		quarto add --no-prompt coatless-quarto/embedio && \
		quarto add --no-prompt gadenbuie/countdown/quarto && \
		quarto add --no-prompt quarto-ext/shinylive && \
		quarto add --no-prompt shafayetShafee/line-highlight

.PHONY: setup
setup:
	make setup-py
	make setup-quarto

.PHONY: clean
clean:
	rm -rf venv

.PHONY: publish
publish:
	quarto publish gh-pages website
