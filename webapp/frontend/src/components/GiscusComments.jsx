import { useEffect, useRef } from 'react'

/**
 * GitHub-powered comments via Giscus.
 * Uses GitHub Discussions API — no database needed.
 *
 * Setup:
 * 1. Enable Discussions on your repo (Settings → General → Features)
 * 2. Install the Giscus app: https://github.com/apps/giscus
 * 3. Go to https://giscus.app and enter your repo to get repoId + categoryId
 * 4. Update the data-repo-id and data-category-id below
 */
export default function GiscusComments({ term }) {
    const ref = useRef(null)

    useEffect(() => {
        // Clean up any existing giscus iframe
        const existing = ref.current?.querySelector('.giscus')
        if (existing) existing.remove()

        const script = document.createElement('script')
        script.src = 'https://giscus.app/client.js'
        script.setAttribute('data-repo', 'KentChun33333/open_memo')
        script.setAttribute('data-repo-id', '')  // ← Get from https://giscus.app
        script.setAttribute('data-category', 'Blog Comments')
        script.setAttribute('data-category-id', '')  // ← Get from https://giscus.app
        script.setAttribute('data-mapping', 'specific')
        script.setAttribute('data-term', term)
        script.setAttribute('data-strict', '0')
        script.setAttribute('data-reactions-enabled', '1')
        script.setAttribute('data-emit-metadata', '0')
        script.setAttribute('data-input-position', 'top')
        script.setAttribute('data-theme', 'dark_dimmed')
        script.setAttribute('data-lang', 'en')
        script.setAttribute('data-loading', 'lazy')
        script.crossOrigin = 'anonymous'
        script.async = true

        ref.current?.appendChild(script)

        return () => {
            const giscus = ref.current?.querySelector('.giscus')
            if (giscus) giscus.remove()
        }
    }, [term])

    return (
        <section className="comments-section">
            <h2>💬 Comments</h2>
            <p className="comments-note">
                Sign in with your <strong>GitHub account</strong> to comment.
                Comments are stored in{' '}
                <a
                    href="https://github.com/KentChun33333/open_memo/discussions"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    GitHub Discussions
                </a>.
            </p>
            <div ref={ref} />
        </section>
    )
}
