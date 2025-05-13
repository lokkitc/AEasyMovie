declare namespace YT {
  interface PlayerOptions {
    height?: string | number
    width?: string | number
    videoId?: string
    playerVars?: {
      autoplay?: 0 | 1
      modestbranding?: 0 | 1
      rel?: 0 | 1
      [key: string]: any
    }
    events?: {
      onReady?: (event: any) => void
      onStateChange?: (event: any) => void
      onError?: (event: any) => void
      [key: string]: ((event: any) => void) | undefined
    }
  }

  class Player {
    constructor(elementId: string, options: PlayerOptions)
    destroy(): void
  }
}

interface Window {
  onYouTubeIframeAPIReady: () => void
  YT: typeof YT
} 