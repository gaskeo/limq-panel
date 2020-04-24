$("#list-tab a").on("click", function (e) {
    e.preventDefault();
    $(this).tab("show");
});

const allowed = ["#list-mainsettings-open", "#list-key-open", "#list-privacy-open"];

$(document).ready(() => {
    var hash = window.location.hash;
    if (allowed.indexOf(hash) >= 0) {
        $(hash).tab("show");
    }
});
