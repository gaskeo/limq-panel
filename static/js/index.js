$("#list-tab a").on("click", function (e) {
    e.preventDefault();
    history.pushState("", "", "#" + this.id);
    $(this).tab("show");
});

const allowed = ["#list-main-settings-open", "#list-keys-open", "#list-mixin-settings-open"];

$(document).ready(() => {
    var hash = window.location.hash;
    if (allowed.indexOf(hash) >= 0) {
        $(hash).tab("show");
    }
});

$("#can-read").change(() => {
    $("#allow-info").toggle();
});

$("#can-write").change(() => {
    $("#allow-info").toggle();
});


$("#allow-info").change(() => {
    $("#selected-info").toggle();
});
