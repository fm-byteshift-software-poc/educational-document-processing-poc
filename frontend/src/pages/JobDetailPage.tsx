import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router'
import api from '@/lib/api'

interface Slide {
  slide_number: number
  section: string
  heading: string
  body: string
}

interface PresentationData {
  presentation_id: string
  title: string
  slides: Slide[]
}

interface JobStatusData {
  job_id: string
  processing_status: string
  document_id: string
  error_message: string | null
}

export default function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const [jobStatus, setJobStatus] = useState<string>('processing')
  const [presentation, setPresentation] = useState<PresentationData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!jobId) return

    let isMounted = true

    const poll = async () => {
      try {
        // 👇 SEM barra no final (casar com a rota do backend)
        const { data } = await api.get<JobStatusData>(`/jobs/${jobId}`)
        setJobStatus(data.processing_status)

        if (data.processing_status === 'completed') {
          // 👇 SEM barra no final
          const { data: presData } = await api.get<PresentationData>(`/presentations/${jobId}`)
          if (isMounted) {
            setPresentation(presData)
            setLoading(false)
          }
        } else if (data.processing_status === 'failed') {
          if (isMounted) {
            setError(data.error_message || 'Processing failed')
            setLoading(false)
          }
        } else {
          setTimeout(poll, 2000)
        }
      } catch (err) {
        if (isMounted) {
          setError('Connection error')
          setLoading(false)
        }
      }
    }

    poll()
    return () => { isMounted = false }
  }, [jobId])

  if (loading && !error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <span className="loading loading-spinner loading-lg text-primary"></span>
        <p className="text-lg opacity-70">Processing document...</p>
        <p className="text-sm opacity-50">Status: {jobStatus}</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-base-100 shadow mt-8">
        <div className="card-body">
          <h2 className="card-title text-error">Processing Failed</h2>
          <p className="opacity-80">{error}</p>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary mt-4">Back to Dashboard</button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">{presentation?.title || 'Presentation'}</h1>
          <span className="badge badge-info mt-2">{jobStatus}</span>
        </div>
        <button onClick={() => navigate('/dashboard')} className="btn btn-ghost">Back</button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {presentation?.slides.map((slide) => (
          <div key={slide.slide_number} className="card bg-base-100 shadow">
            <div className="card-body">
              <div className="flex justify-between items-start">
                <span className="badge badge-outline">Slide {slide.slide_number}</span>
                <span className="text-xs opacity-50 uppercase">{slide.section}</span>
              </div>
              <h3 className="card-title mt-4">{slide.heading}</h3>
              <p className="text-sm opacity-80 whitespace-pre-line mt-2">{slide.body}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}