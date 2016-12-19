/**
 * Created by mruizo on 19/07/16.
 */

$(document).ready(function () {
    var select_filter_type = $("select#id_filter_type");
    var select_ad_converter = $("select#id_ad_converter");
    var select_preamplifier = $("select#id_amplifier");
    var select_electrodo = $("select#id_electrodo");

    select_filter_type.change(function(){

        var filter_type_id = $(this).val();
        var description_field = $("#id_description");

        var url = "/experiment/filter/" + filter_type_id + "/attributes";

        if (filter_type_id == "") {
            description_field.prop('value', "");
        }else{
            $.getJSON(url, function (filter) {
                description_field.prop('value', filter['description']);
            });
        }
    });
    
    select_ad_converter.change(function () {
       var ad_converter_id = $(this).val();
       var description_field = $("#id_description");
        
       var url = "/experiment/equipment/" + ad_converter_id + "/attributes";
        
       if(ad_converter_id == ""){
           description_field.prop('value', "");
       }else{
           $.getJSON(url, function (ad_converter) {
               description_field.prop('value', ad_converter['description']);
           })
       }
    });
    
    select_preamplifier.change(function () {
       var preamplifier_id = $(this).val();
       var description_field = $("#id_description");
        
       var url = "/experiment/equipment/" + preamplifier_id + "/attributes";
        
       if(preamplifier_id == ""){
           description_field.prop('value', "");
       }else{
           $.getJSON(url, function (preamplifier) {
               description_field.prop('value', preamplifier['description']);
           })
       }
    });
    
    select_electrodo.change(function () {
       var electrodo_id = $(this).val();
       var description_field = $("#id_description");
        
       var url = "/experiment/emg_setting/get_electrode_model/" + electrodo_id + "/attributes";
        
       if(electrodo_id == ""){
           description_field.prop('value', "");
       }else{
           $.getJSON(url, function (electrodo) {
               description_field.prop('value', electrodo['description']);
           })
       }
    });
    
});