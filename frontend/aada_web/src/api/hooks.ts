export {
  useLoginApiAuthLoginPost as useLoginMutation,
  useMeApiAuthMeGet as useMeQuery,
} from './generated/auth/auth';

export {
  useListProgramsApiProgramsGet as useProgramsQuery,
  useListModulesApiProgramsProgramIdModulesGet as useProgramModulesQuery,
} from './generated/programs/programs';

export {
  useGetModuleApiModulesModuleIdGet as useModuleContentQuery,
} from './generated/modules/modules';

export {
  useListExternshipsApiExternshipsGet as useExternshipsQuery,
} from './generated/externships/externships';

export {
  useListWithdrawalsApiFinanceWithdrawalsGet as useWithdrawalsQuery,
  useListRefundsApiFinanceRefundsGet as useRefundsQuery,
} from './generated/finance/finance';

export {
  useListCredentialsApiCredentialsGet as useCredentialsQuery,
  useCreateCredentialApiCredentialsPost as useCreateCredentialMutation,
} from './generated/credentials/credentials';

export {
  useListEnrollmentsApiEnrollmentsGet as useEnrollmentsQuery,
} from './generated/enrollments/enrollments';

export {
  useListTranscriptsApiTranscriptsGet as useTranscriptsQuery,
} from './generated/transcripts/transcripts';
