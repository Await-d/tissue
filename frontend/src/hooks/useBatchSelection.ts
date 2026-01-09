import { useState, useCallback, useMemo } from 'react';

export interface UseBatchSelectionOptions<T> {
    items: T[];
    getItemId: (item: T) => string | number;
}

export interface UseBatchSelectionReturn<T> {
    selectedIds: Set<string | number>;
    selectedItems: T[];
    isSelected: (id: string | number) => boolean;
    toggleSelection: (id: string | number) => void;
    toggleAll: () => void;
    selectRange: (startId: string | number, endId: string | number) => void;
    clearSelection: () => void;
    isAllSelected: boolean;
    selectedCount: number;
}

/**
 * Custom hook for managing batch selection state
 *
 * @example
 * ```tsx
 * const {
 *   selectedIds,
 *   selectedItems,
 *   isSelected,
 *   toggleSelection,
 *   toggleAll,
 *   selectRange,
 *   clearSelection,
 *   selectedCount
 * } = useBatchSelection({
 *   items: videos,
 *   getItemId: (video) => video.path
 * });
 * ```
 */
export function useBatchSelection<T>({
    items,
    getItemId
}: UseBatchSelectionOptions<T>): UseBatchSelectionReturn<T> {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());
    const [lastSelectedId, setLastSelectedId] = useState<string | number | null>(null);

    const isSelected = useCallback(
        (id: string | number) => selectedIds.has(id),
        [selectedIds]
    );

    const toggleSelection = useCallback(
        (id: string | number) => {
            setSelectedIds(prev => {
                const newSet = new Set(prev);
                if (newSet.has(id)) {
                    newSet.delete(id);
                } else {
                    newSet.add(id);
                }
                return newSet;
            });
            setLastSelectedId(id);
        },
        []
    );

    const toggleAll = useCallback(() => {
        if (selectedIds.size === items.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(items.map(getItemId)));
        }
    }, [items, getItemId, selectedIds.size]);

    const selectRange = useCallback(
        (startId: string | number, endId: string | number) => {
            const startIndex = items.findIndex(item => getItemId(item) === startId);
            const endIndex = items.findIndex(item => getItemId(item) === endId);

            if (startIndex === -1 || endIndex === -1) return;

            const [minIndex, maxIndex] = [
                Math.min(startIndex, endIndex),
                Math.max(startIndex, endIndex)
            ];

            setSelectedIds(prev => {
                const newSet = new Set(prev);
                for (let i = minIndex; i <= maxIndex; i++) {
                    newSet.add(getItemId(items[i]));
                }
                return newSet;
            });
        },
        [items, getItemId]
    );

    const clearSelection = useCallback(() => {
        setSelectedIds(new Set());
        setLastSelectedId(null);
    }, []);

    const selectedItems = useMemo(
        () => items.filter(item => selectedIds.has(getItemId(item))),
        [items, selectedIds, getItemId]
    );

    const isAllSelected = useMemo(
        () => items.length > 0 && selectedIds.size === items.length,
        [items.length, selectedIds.size]
    );

    return {
        selectedIds,
        selectedItems,
        isSelected,
        toggleSelection,
        toggleAll,
        selectRange,
        clearSelection,
        isAllSelected,
        selectedCount: selectedIds.size
    };
}
