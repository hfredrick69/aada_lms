import { defineConfig } from 'orval';

export default defineConfig({
  aada: {
    input: '../backend/openapi.json',
    output: {
      target: 'src/api/generated/index.ts',
      schemas: 'src/api/generated/models',
      client: 'react-query',
      mode: 'tags-split',
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: './src/api/http-client.ts',
          name: 'axiosInstance',
        },
      },
    },
    hooks: {
      useQuery: true,
      useMutation: true,
    },
    override: {
      operations: {
        login_api_auth_login_post: {
          name: 'login',
        },
        me_api_auth_me_get: {
          name: 'getAuthMe',
        },
        list_programs_api_programs_get: {
          name: 'listPrograms',
        },
        list_modules_api_programs__program_id__modules_get: {
          name: 'listProgramModules',
        },
        list_externships_api_externships_get: {
          name: 'listExternships',
        },
        list_refunds_api_finance_refunds_get: {
          name: 'listRefunds',
        },
        list_withdrawals_api_finance_withdrawals_get: {
          name: 'listWithdrawals',
        },
        list_credentials_api_credentials_get: {
          name: 'listCredentials',
        },
        create_credential_api_credentials_post: {
          name: 'createCredential',
        },
        list_enrollments_api_enrollments_get: {
          name: 'listEnrollments',
        },
        list_transcripts_api_transcripts_get: {
          name: 'listTranscripts',
        },
      },
    },
  },
});
