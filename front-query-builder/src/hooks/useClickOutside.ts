import { useEffect, useRef } from 'react';

type HandledEvents = 'mousedown' | 'touchstart';

export function useClickOutside<T extends HTMLElement>(callback: () => void) {
  const ref = useRef<T>(null);

  const latestCallbackRef = useRef(callback);

  useEffect(() => {
    latestCallbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    function handleClick(event: MouseEvent | TouchEvent) {
      const target = event.target as Node;
      if (!target) {
        return;
      }

      if (ref.current && !ref.current.contains(target)) {
        latestCallbackRef.current();
      }
    }

    const events: HandledEvents[] = ['mousedown', 'touchstart'];

    events.forEach((event) => {
      document.addEventListener(event, handleClick);
    });

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleClick);
      });
    };
  }, [ref]);

  return ref;
}
