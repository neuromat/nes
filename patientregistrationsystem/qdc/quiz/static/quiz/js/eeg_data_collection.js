$(document).ready(function () {

	var $id_file_format = $("#id_file_format");

	$id_file_format.each(function() {
		if ($("#id_file_format option:selected").text() == "Other")
            $id_file_format.parents('.row').next().show();
		else
			$id_file_format.parents('.row').next().hide();
	});

    $id_file_format.on('change', (function() {
		if ($("#id_file_format option:selected").text() == "Other")
            $id_file_format.parents('.row').next().show();
		else
			$id_file_format.parents('.row').next().hide();
	}));

});
