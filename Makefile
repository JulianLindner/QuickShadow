# Basic Plugin Metadata
PLUGINNAME = QuickShadow
PY_FILES = __init__.py QuickShadow.py QuickShadow_provider.py QuickShadow_algorithm.py QuickAttic_algorithm.py 
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
	rm -rf /tmp/$(PLUGINNAME)
	rm -f "$(PLUGINNAME).zip"
	mkdir -p /tmp/$(PLUGINNAME)
	# Copy files to temporary folder
	cp -r $(PY_FILES) $(EXTRAS) /tmp/$(PLUGINNAME)/
	[ -d i18n ] && cp -r i18n /tmp/$(PLUGINNAME)/ || true
	# Use quotes around $(CURDIR) to handle the spaces in your iCloud path
	cd /tmp && zip -r "$(CURDIR)/$(PLUGINNAME).zip" $(PLUGINNAME)
	rm -rf /tmp/$(PLUGINNAME)
	@echo "Zip created successfully at $(CURDIR)/$(PLUGINNAME).zip"

# Remove local deployment
clean:
	@echo "Removing $(PLUGINNAME) from $(QGISDIR)"
	rm -Rf "$(QGISDIR)/$(PLUGINNAME)"