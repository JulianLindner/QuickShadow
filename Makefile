# Basic Plugin Metadata
PLUGINNAME = QuickShadow
PY_FILES = __init__.py QuickShadow.py QuickShadow_provider.py QuickShadow_algorithm.py
EXTRAS = metadata.txt icon.svg
LOCALES = en

# QGIS Directory (Adjust based on your OS)
# Mac: Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
# Linux: .local/share/QGIS/QGIS3/profiles/default/python/plugins/
QGISDIR = $(HOME)/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins

.PHONY: default deploy zip clean

default:
	@echo "Commands: deploy, zip, clean"

# Deploy to local QGIS profile for testing
deploy:
	@echo "Deploying $(PLUGINNAME) to $(QGISDIR)"
	mkdir -p "$(QGISDIR)/$(PLUGINNAME)"
	cp -vf $(PY_FILES) "$(QGISDIR)/$(PLUGINNAME)"
	cp -vf $(EXTRAS) "$(QGISDIR)/$(PLUGINNAME)"
	# Copy translations if the folder exists
	[ -d i18n ] && cp -vfr i18n "$(QGISDIR)/$(PLUGINNAME)" || true

# Create a zip bundle for sharing or uploading to the QGIS repo
zip:
	@echo "Creating $(PLUGINNAME).zip..."
	rm -f $(PLUGINNAME).zip
	# Created zip in the current directory 
	zip -r $(PLUGINNAME).zip $(PY_FILES) $(EXTRAS) $$( [ -d i18n ] && echo "i18n" )

# Remove local deployment
clean:
	@echo "Removing $(PLUGINNAME) from $(QGISDIR)"
	rm -Rf "$(QGISDIR)/$(PLUGINNAME)"