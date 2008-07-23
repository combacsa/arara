
$(document).ready(function(){
    var user_popup = $("#user_popup");
    user_popup.hide();
    user_popup.addClass("absolute");

    $("#user_popup li").hover(
    function(event) {
        $(this).addClass("user_popup_menu_hover");
    },
    function(event) {
        $(this).removeClass("user_popup_menu_hover");
    });

    $(".username").hover(
    function(event) {
        $(this).addClass("username_highlight");
    },
    function(event) {
        $(this).removeClass("username_highlight");
    });

    var username;
    $(".username").click(function(event) {
        username = $(this).text();
        $("#user_popup #user_popup_username").text("User: " + username);

        $("#user_popup").css("top", $(this).offset()["top"] + $(this).height())
        $("#user_popup").css("left", $(this).offset()["left"])

        $("#user_popup").show("fast");
        event.stopPropagation(); 
    });

    $("#user_popup_send_message").click(function(event) {
        alert("hello, world!");
        event.preventDefault();
    });

    $("#user_popup_user_information").click(function(event) {
        alert("hello, world!");
        event.preventDefault();
    });

    $("#user_popup_add_blacklist").click(function(event) {
        $.post("/blacklist/add/", {blacklist_id: username},
            function(data) {
                alert("Added " + username + " to blacklist.");
            }
        );
        event.preventDefault();
    });

    $("html").click(function(event) {
        $("#user_popup").hide("fast");
    });
});