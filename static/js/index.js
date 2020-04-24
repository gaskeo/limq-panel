$("#list-tab a").on("click", function (e) {
    e.preventDefault();
    $(this).tab("show");
});

const allowed = ["#list-main-settings-open", "#list-keys-open", "#list-privacy-settings-open"];

$(document).ready(() => {
    var hash = window.location.hash;
    if (allowed.indexOf(hash) >= 0) {
        $(hash).tab("show");
    }
});
