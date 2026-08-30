// Script de uso único: gera os PNGs de ícone da PWA a partir do favicon.svg
// (mesma marca "C com gráfico e moeda" usada em toda a app). Não faz parte
// do build normal — corre-se manualmente quando a marca mudar.
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const __dirname = dirname(fileURLToPath(import.meta.url))
const publicDir = resolve(__dirname, '../public')
const svgBuffer = readFileSync(resolve(publicDir, 'favicon.svg'))

const WHITE = '#ffffff'

async function renderMark(size) {
  return sharp(svgBuffer, { density: 384 }).resize(size, size).png().toBuffer()
}

async function iconOnWhite(size, markSize) {
  const mark = await renderMark(markSize)
  const offset = Math.round((size - markSize) / 2)
  return sharp({
    create: { width: size, height: size, channels: 4, background: WHITE },
  })
    .composite([{ input: mark, left: offset, top: offset }])
    .png()
    .toBuffer()
}

const jobs = [
  // Ícones "any" (transparentes) — usados pelo browser/launcher normal.
  { name: 'pwa-192x192.png', build: () => renderMark(192) },
  { name: 'pwa-512x512.png', build: () => renderMark(512) },
  // Maskable — a marca ocupa ~55% do canvas para caber na "safe zone"
  // quando o launcher (Android) recorta em círculo/squircle/etc.
  { name: 'maskable-icon-512x512.png', build: () => iconOnWhite(512, 282) },
  // iOS não deteta bem PNGs transparentes (mete fundo preto) — fundo sólido.
  { name: 'apple-touch-icon.png', build: () => iconOnWhite(180, 130) },
]

for (const job of jobs) {
  const buffer = await job.build()
  const outPath = resolve(publicDir, job.name)
  await sharp(buffer).toFile(outPath)
  console.log('gerado:', outPath)
}
