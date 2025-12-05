import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Header } from './Header';
import { ProgressBar } from './ProgressBar';
import { useAuth } from '../../hooks/useAuth';
import { Stage } from '../../types/documento';
import { DocumentManagementProvider, useDocumentManagementContext } from '../../hooks/DocumentManagementContext';
import { useEffect, useState } from 'react';
import { getMinhaMatricula } from '../../services/matricula';

const DashboardLayoutInner = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, handleLogout, isLoggedIn, isInitializing } = useAuth();

    const { documents } = useDocumentManagementContext();

    const getCurrentStage = (): Stage => {
        if (location.pathname.includes('/review')) return 'review';
        if (location.pathname.includes('/approved')) return 'approved';
        return 'upload';
    };

    const [canViewEnrollmentFromApi, setCanViewEnrollmentFromApi] = useState<boolean | null>(null);

    useEffect(() => {
        const fetch = async () => {
            const token = user?.token;
            if (!token) {
                setCanViewEnrollmentFromApi(null);
                return;
            }
            try {
                const matricula = await getMinhaMatricula(token);
                if (matricula) {
                    const statusRaw = (matricula as any).statusMatricula ?? (matricula as any).status ?? '';
                    setCanViewEnrollmentFromApi(String(statusRaw).toLowerCase() === 'aprovado');
                } else {
                    setCanViewEnrollmentFromApi(null);
                }
            } catch (e) {
                setCanViewEnrollmentFromApi(null);
            }
        };
        fetch();
    }, [user?.token, documents]);

    const currentStage = getCurrentStage();

    if (isInitializing) {
        return <div>Carregando...</div>;
    }

    if (!user) {
        return <div>Carregando...</div>;
    }

    const canViewEnrollmentFallback =
        documents.some(doc => doc.tipo === '1' && doc.status === 'aprovado') &&
        documents.some(doc => doc.tipo === '3' && doc.status === 'aprovado');

    const canViewEnrollment = canViewEnrollmentFromApi === true;

    const canProceed = documents.some(doc => 
        doc.status === 'enviado' || 
        doc.status === 'revisao' || 
        doc.status === 'aprovado'
    );

    const handleNavigateToNext = () => {
        if (currentStage === 'upload') {
            navigate('/dashboard/review');
        }
        if (currentStage === 'review' && canViewEnrollment) {
            navigate('/dashboard/approved');
        }
    };

    const handleNavigateToPrevious = () => {
        if (currentStage === 'review') {
            navigate('/dashboard/upload');
        } else if (currentStage === 'approved') {
            navigate('/dashboard/review');
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Header onLogout={() => { handleLogout(); navigate('/login'); }} />

            <div className="max-w-7xl mx-auto px-4 py-8">
                <ProgressBar
                    currentStage={currentStage}
                    onNextStage={handleNavigateToNext}
                    onPreviousStage={handleNavigateToPrevious}
                    canProceed={canProceed}
                    canViewEnrollment={canViewEnrollment}
                    hasUploadedFiles={documents.some(doc => doc.status !== 'pendente')}
                />

                <main className="mt-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export const DashboardLayout = () => {
    return (
        <DocumentManagementProvider>
            <DashboardLayoutInner />
        </DocumentManagementProvider>
    );
};