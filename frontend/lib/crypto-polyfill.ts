// Polyfill para crypto.randomUUID
if (typeof window !== 'undefined') {
  if (typeof crypto === 'undefined') {
    // @ts-ignore
    window.crypto = {}
  } else if (typeof crypto.randomUUID !== 'function') {
    // @ts-ignore
    crypto.randomUUID = function() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    };
  }
}

export {}; 