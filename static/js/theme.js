const Theme = 'theme'
const availableThemes = {
    light: 'light',
    dark: 'dark',
    system: 'system'
}

function initTheme() {
    const currentTheme = getTheme()
    setTheme(currentTheme)
    setLogo()
}


function getTheme() {
    const currentTheme = localStorage.getItem(Theme)
    if (currentTheme === availableThemes.light || currentTheme === availableThemes.dark) {
        return currentTheme
    }

    setTheme(availableThemes.system)
    return availableThemes.system
}

function getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return  availableThemes.dark
    } else {
        return  availableThemes.light
    }
}

function setTheme(theme) {
    let dataTheme;
    if (!(theme === availableThemes.light || theme === availableThemes.dark)) {
        dataTheme = getSystemTheme()
    } else {
        dataTheme = theme
    }

    localStorage.setItem(Theme, theme)
    document.documentElement.setAttribute("data-theme", dataTheme);
}

function toggleTheme() {
    const currentTheme = localStorage.getItem(Theme)
    const newTheme = currentTheme === availableThemes.dark ? availableThemes.light : availableThemes.dark

    setTheme(newTheme)
}

window.onload = initTheme
