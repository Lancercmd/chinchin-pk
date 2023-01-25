import 'zx/globals'
import { Knex, knex } from 'knex'

const EXAMPLE_JSON = {
  qq: 123456789,
  length: 23.34,
  register_time: '2023-01-25 02:26:52',
  daily_lock_count: 6,
  daily_pk_count: 6,
  daily_glue_count: 6,
  latest_daily_lock: '2023-01-25 02:26:52',
  latest_daily_pk: '2023-01-25 01:00:00',
  latest_daily_glue: '2023-01-25 02:26:52',
  pk_time: '2000-01-01 00:00:00',
  pked_time: '2020-01-01 00:00:01',
  glueing_time: '2023-01-25 02:26:52',
  glued_time: '2023-01-25 02:26:52',
  locked_time: '2023-01-25 02:26:52',
}

const run = async () => {
  const DATABASE_PATH = path.join(__dirname, './data.sqlite')
  const SQL_FILE = path.join(__dirname, './data_migrate.sql')
  const config: Knex.Config = {
    client: 'better-sqlite3',
    connection: {
      filename: DATABASE_PATH,
    },
  }
  const ins = knex(config)
  const sql: string[] = []

  try {
    // Create a table if not exists
    const createSql = await ins.schema
      .createTableIfNotExists('users', (table) => {
        // create primary key, name is qq
        table.bigint('qq').primary()
        table.float('length')
        ;['daily_lock_count', 'daily_pk_count', 'daily_glue_count'].forEach(
          (key) => {
            table.integer(key)
          }
        )
        ;[
          'register_time',
          'latest_daily_lock',
          'latest_daily_pk',
          'latest_daily_glue',
          'pk_time',
          'pked_time',
          'glueing_time',
          'glued_time',
          'locked_time',
        ].forEach((key) => {
          table.string(key)
        })
      })
      .toSQL()
    // @ts-expect-error
    sql.push(createSql[0].sql)
    // Insert data
    const insertSql = await ins('users').insert(EXAMPLE_JSON).toSQL()
    sql.push(insertSql.sql)
    // select single data by qq
    const selectSql = await ins('users')
      .select('*')
      .where('qq', 123456789)
      .toSQL()
    sql.push(selectSql.sql)
    // update single data by qq
    const updateSql = await ins('users')
      .update(EXAMPLE_JSON)
      .where('qq', 123456789)
      .toSQL()
    sql.push(updateSql.sql)
    // write
    fs.writeFileSync(SQL_FILE, sql.join(';\n') + ';\n', 'utf-8')
  } catch (e) {
    console.error(e)
  } finally {
    await ins.destroy()
  }
}

run()
