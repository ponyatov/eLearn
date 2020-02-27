CWD    = $(CURDIR)
MODULE = $(notdir $(CWD))

NOW = $(shell date +%d%m%y)
REL = $(shell git rev-parse --short=4 HEAD)

PIP = $(CWD)/bin/pip3
PY  = $(CWD)/bin/python3



.PHONY: all
all: $(PY) ./$(MODULE).py $(MODULE).ini
	$^



.PHONY: install
install: debian $(PIP)
	$(PIP) install -r requirements.txt
	$(MAKE) requirements.txt

.PHONY: update
update: debian $(PIP)
	$(PIP) install -U -r requirements.txt
	$(MAKE) requirements.txt

$(PIP) $(PY):
	python3 -m venv .
	$(CWD)/bin/pip3 install -U pip

.PHONY: requirements.txt
requirements.txt: $(PIP)
	$< freeze | grep -v 0.0.0 > $@

.PHONY: debian
debian:
	sudo apt update
	sudo apt install -u python3 python3-pyqt5



.PHONY: merge release zip

MERGE  = Makefile README.md .gitignore $(MODULE).* static templates

merge:
	git checkout master
	git checkout shadow -- $(MERGE)

release:
	git tag $(NOW)-$(REL)
	git push -v && git push -v --tags
	git checkout shadow

zip:
	git archive --format zip --output $(MODULE)_src_$(NOW)_$(REL).zip HEAD
