import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import mdx from '@mdx-js/rollup'

import remarkFrontmatter from 'remark-frontmatter'
import remarkMdxFrontmatter from 'remark-mdx-frontmatter'
import remarkMath from 'remark-math'
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex'

export default defineConfig({
    plugins: [
        { enforce: 'pre', ...mdx({ remarkPlugins: [remarkGfm, remarkFrontmatter, remarkMdxFrontmatter, remarkMath], rehypePlugins: [rehypeKatex] }) },
        react({ include: /\.(jsx|js|mdx|md|tsx|ts)$/ })
    ],
    server: {
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://localhost:8080',
                changeOrigin: true,
            },
            '/assets': {
                target: 'http://localhost:8080',
                changeOrigin: true,
            },
            '/nanobot-status': {
                target: 'http://localhost:8080',
                changeOrigin: true,
            },
        },
    },
})
