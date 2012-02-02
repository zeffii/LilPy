from pprint import pprint

doc = mainframe.get_document()
player = doc.get_player()

def getURI(plugin_name):
	uriList = []
	for i in range(player.get_pluginloader_count()):
		uri = player.get_pluginloader(i).get_uri()
		if uri.lower().find(plugin_name) >= 0:
			uriList.append(uri)
	return uriList

pprint(getURI("dist"))
