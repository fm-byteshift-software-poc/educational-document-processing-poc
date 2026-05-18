import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router'
import api from '@/lib/api'

interface Document {
  id: string
  filename: string
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  uploaded_at: string
  job_id?: string | null
}

export default function DashboardPage() {
  const [docs, setDocs] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const fetchDocs = async () => {
    try {
      const { data } = await api.get('/documents/')
      setDocs(data.documents)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    }
  }

  // Polling automático: se houver processamento, atualiza a lista a cada 3s
  useEffect(() => {
    const isProcessing = docs.some(d => d.status === 'processing')
    if (isProcessing) {
      const interval = setInterval(fetchDocs, 3000)
      return () => clearInterval(interval)
    }
  }, [docs])

  useEffect(() => {
    fetchDocs()
  }, [])

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const fileInput = form.elements.namedItem('file') as HTMLInputElement
    const file = fileInput?.files?.[0]
    if (!file) return

    setUploading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      fileInput.value = ''
      await fetchDocs()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleProcess = async (docId: string) => {
    try {
      await api.post('/jobs/', { document_id: docId })
      await fetchDocs()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start job')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Upload Document</h2>
          <form onSubmit={handleUpload} className="flex gap-2 mt-2">
            <input type="file" name="file" accept=".pdf,.txt" className="file-input file-input-bordered w-full" required />
            <button type="submit" className="btn btn-primary" disabled={uploading}>
              {uploading ? <span className="loading loading-spinner"></span> : 'Upload'}
            </button>
          </form>
        </div>
      </div>

      {error && <div className="alert alert-error"><span>{error}</span></div>}

      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Your Documents</h2>
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((doc) => (
                  <tr key={doc.id}>
                    <td className="font-medium">{doc.filename}</td>
                    <td>
                      <span className={`badge ${
                        doc.status === 'completed' ? 'badge-success' :
                        doc.status === 'processing' ? 'badge-warning loading-dots' :
                        doc.status === 'failed' ? 'badge-error' : 'badge-ghost'
                      }`}>
                        {doc.status}
                      </span>
                    </td>
                    <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                    <td>
                      <div className="flex gap-2">
                        {doc.status === 'uploaded' && (
                          <button onClick={() => handleProcess(doc.id)} className="btn btn-sm btn-secondary">
                            Process
                          </button>
                        )}
                        {doc.status === 'completed' && doc.job_id && (
                          <button onClick={() => navigate(`/job/${doc.job_id}`)} className="btn btn-sm btn-primary">
                            View
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {docs.length === 0 && (
                  <tr><td colSpan={4} className="text-center opacity-50">No documents uploaded yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}