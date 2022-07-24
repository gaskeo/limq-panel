function setLogo() {
    const logoContainer = document.getElementById('lithium-container')
    const logo = document.createElement('img')
    logo.alt = 'LiMQ'
    if (document.documentElement.getAttribute('data-theme') === availableThemes.light) {
        logo.src = "../static/images/limq-for-white.svg"
    } else {
        logo.src = "../static/images/limq-for-dark.svg"
    }
    logoContainer.appendChild(logo)
}