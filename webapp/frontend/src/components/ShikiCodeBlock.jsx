import React, { useEffect, useState } from 'react';
import { codeToHtml } from 'shiki';

export function ShikiCodeBlock({ language = 'javascript', children, theme = 'vitesse-dark' }) {
    const [html, setHtml] = useState('');
    const code = String(children).trim();

    useEffect(() => {
        let isMounted = true;

        async function highlight() {
            try {
                const result = await codeToHtml(code, {
                    lang: language,
                    theme: theme,
                });
                if (isMounted) {
                    setHtml(result);
                }
            } catch (error) {
                console.error("Shiki Error:", error);
                if (isMounted) {
                    // Fallback to raw text if syntax highlighting fails
                    setHtml(`<pre><code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`);
                }
            }
        }

        highlight();

        return () => { isMounted = false; };
    }, [code, language, theme]);

    return (
        <div
            className="shiki-code-block"
            style={{ margin: '1rem 0', borderRadius: '8px', overflow: 'hidden' }}
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
}
