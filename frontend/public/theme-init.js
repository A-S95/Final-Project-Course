// Aplica o tema guardado antes do primeiro paint — sem isto, a página pintava
// sempre com o tema do sistema por uma fração de segundo e só depois "saltava"
// para a escolha manual do utilizador (guardada em localStorage), assim que o
// React montava o ThemeProvider.
// Ficheiro à parte (não inline no index.html) para a CSP poder usar script-src 'self'.
try {
  var storedTheme = localStorage.getItem('centisible-theme')
  if (storedTheme === 'light' || storedTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', storedTheme)
  }
} catch {
  /* localStorage indisponível (modo privado) — segue o tema do sistema */
}
