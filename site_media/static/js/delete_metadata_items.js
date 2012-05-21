    function delete_property(prop_id) {
		var resp = $.ajax( { 
			type: "POST", 
			url: '../../../metadata/property_delete/', 
			data: ({ prop_id:prop_id, action:'property_delete' }), 
            success: function(data) { 
                var t = $.tree.focused(); 
                if(t.selected) {
                    var load_url = '../../../metadata/properties_list/' + t.selected[0].id + '/';
                    $('#properties_area').load(load_url, function() {
                    })
                }
            },
		});
     };
    function remove_object(section_id, obj_id, obj_type) {
        if (obj_type == "dataset") {
		    var resp = $.ajax( {
			    type: "POST", 
			    url: '../../../metadata/remove_dataset/', 
			    data: ({ section_id:section_id, dataset_id:obj_id, action:'remove_dataset' }), 
                success: function(data) { 
                    var t = $.tree.focused(); 
                    if(t.selected) {
                        var load_url = '../../../metadata/properties_list/' + t.selected[0].id + '/';
                        $('#properties_area').load(load_url, function() {
                        })
                    }
                },
		    });
        };
        if (obj_type == "datafile") {
		    var resp = $.ajax( {
			    type: "POST", 
			    url: '../../../metadata/remove_datafile/', 
			    data: ({ section_id:section_id, datafile_id:obj_id, action:'remove_datafile' }), 
                success: function(data) { 
                    var t = $.tree.focused(); 
                    if(t.selected) {
                        var load_url = '../../../metadata/properties_list/' + t.selected[0].id + '/';
                        $('#properties_area').load(load_url, function() {
                        })
                    }
                },
		    });
        };
        if (obj_type == "timeseries") {
		    var resp = $.ajax( {
			    type: "POST", 
			    url: '../../../metadata/remove_timeseries/', 
			    data: ({ section_id:section_id, timeseries_id:obj_id, action:'remove_timeseries' }), 
                success: function(data) { 
                    var t = $.tree.focused(); 
                    if(t.selected) {
                        var load_url = '../../../metadata/properties_list/' + t.selected[0].id + '/';
                        $('#properties_area').load(load_url, function() {
                        })
                    }
                },
		    });
        };
     };
