function unselectAll() {
	var obj = document.getElementById("id_shared_with");
	for (var loop=0; loop < obj.options.length; loop++) {
	obj.options[loop].selected = false;
	}
};
