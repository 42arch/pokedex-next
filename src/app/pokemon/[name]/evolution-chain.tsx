import { Separator } from '@/components/ui/separator'
import type { EvolutionChain } from '@/types'
import Image from 'next/image'
import Link from 'next/link'

interface Props {
  data: EvolutionChain[]
}

function EvolutionChain({ data }: Props) {
  return (
    <div className='flex flex-col items-center gap-2'>
      {data.map((chain, index) => (
        <div key={index}>
          <div className='flex flex-col flex-wrap items-center justify-center gap-12'>
            {chain.map((poke, idx) => (
              <div
                key={idx}
                className='relative flex w-[180px] flex-col items-center justify-center'
              >
                {poke.stage === '1阶进化' || poke.stage === '2阶进化' ? (
                  <div
                    style={{
                      background: '#ffcc00'
                    }}
                    className='nodrag nopan -translate-y-[20px] text-center text-xs'
                  >
                    {poke.text}
                  </div>
                ) : (
                  ''
                )}
                <Link href={poke.name}>
                  <Image
                    src={`/images/dream/${poke.image}`}
                    alt={poke.name}
                    width={100}
                    height={100}
                  />
                  <p className='mt-2 text-center text-sm'>{poke?.name}</p>
                </Link>

                <p className='text-center text-sm'>{poke.form_name}</p>
                <p className='mt-2 rounded-full bg-muted px-2 text-center text-xs text-muted-foreground'>
                  {poke?.stage}
                </p>
              </div>
            ))}
          </div>
          {index !== data.length - 1 && <Separator className='my-4 mt-6' />}
        </div>
      ))}
    </div>
  )
}

export default EvolutionChain
