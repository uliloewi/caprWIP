type RequestOptions = RequestInit | undefined;

declare global {
    interface Window {
        __CAPR_API_BASE__?: string;
    }
}

let resolvedBase: string | null = null;

const candidateBases = (() => {
    const bases: string[] = [];
    const globalScope: Record<string, unknown> = typeof window !== 'undefined' ? (window as unknown as Record<string, unknown>) : {};

    const configured = globalScope.__CAPR_API_BASE__ as string | undefined;
    if (configured && typeof configured === 'string') {
        bases.push(configured);
    }

    bases.push('/api');

    if (typeof window !== 'undefined') {
        const { protocol, hostname } = window.location;
        bases.push(`${protocol}//${hostname}:5001`);
        bases.push(`${protocol}//${hostname}:5000`);
    }

    const seen = new Set<string>();
    return bases.filter(base => {
        if (!base) return false;
        if (seen.has(base)) return false;
        seen.add(base);
        return true;
    });
})();

export function getResolvedApiBase(): string | null {
    return resolvedBase;
}

export async function apiFetch(path: string, init?: RequestOptions): Promise<Response> {
    const bases = resolvedBase ? [resolvedBase] : candidateBases;
    let lastError: unknown = null;

    for (const base of bases) {
        const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
        try {
            const response = await fetch(url, init);

            if (!response.ok) {
                if (response.status === 404 || response.status === 502 || response.status === 503 || response.status === 504) {
                    lastError = new Error(`Request to ${url} failed with status ${response.status}`);
                    continue;
                }
            }

            resolvedBase = base;
            return response;
        } catch (err) {
            lastError = err;
        }
    }

    throw lastError instanceof Error ? lastError : new Error('Unable to reach API');
}
