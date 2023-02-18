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

const USER_INFO_TABLE = {
  qq: 123456789,
  latest_speech_nickname: '',
  latest_speech_group: 987654321,
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
    // get all data counts
    const countSql = await ins.table('users').count().toSQL()
    sql.push(countSql.sql)
    // sort by length max 10
    const sortSql = await ins('users')
      .select('*')
      .orderBy('length', 'desc')
      .limit(10)
      .toSQL()
    sql.push(sortSql.sql)

    sql.push('-- User Info Table --')
    const createSqlWithUserInfo = await ins.schema
      .createTableIfNotExists('info', (table) => {
        table.bigint('qq').primary()
        table.string('latest_speech_nickname')
        table.bigint('latest_speech_group')
      })
      .toSQL()
    // @ts-expect-error
    sql.push(createSqlWithUserInfo[0].sql)
    const insertSqlWithUserInfo = await ins('info')
      .insert(USER_INFO_TABLE)
      .toSQL()
    sql.push(insertSqlWithUserInfo.sql)
    const selectSqlWithUserInfo = await ins('info')
      .select('*')
      .where('qq', 123456789)
      .toSQL()
    sql.push(selectSqlWithUserInfo.sql)
    // delete
    const deleteSqlWithUserInfo = await ins('info')
      .where('qq', 123456789)
      .del()
      .toSQL()
    sql.push(deleteSqlWithUserInfo.sql)

    sql.push('-- Rebirth Table --')
    const createSqlWithRebirth = await ins.schema
      .createTableIfNotExists('rebirth', (table) => {
        table.bigint('qq').primary()
        table.string('latest_rebirth_time')
        table.integer('level')
      })
      .toSQL()
    // @ts-expect-error
    sql.push(createSqlWithRebirth[0].sql)
    const insertSqlWithRebirth = await ins('rebirth')
      .insert({
        qq: 123456789,
        latest_rebirth_time: '2023-01-25 02:26:52',
        level: 1,
      })
      .toSQL()
    sql.push(insertSqlWithRebirth.sql)
    const selectSqlWithRebirth = await ins('rebirth')
      .select('*')
      .where('qq', 123456789)
      .toSQL()
    sql.push(selectSqlWithRebirth.sql)
    // delete
    const deleteSqlWithRebirth = await ins('rebirth')
      .where('qq', 123456789)
      .del()
      .toSQL()
    sql.push(deleteSqlWithRebirth.sql)

    // badge table
    sql.push('-- Badge Table --')
    const createSqlWithBadge = await ins.schema
      .createTableIfNotExists('badge', (table) => {
        table.bigint('qq').primary()
        table.string('badge_ids')
        // glue
        table.bigint('glue_me_count')
        table.bigint('glue_target_count')
        table.bigint('glue_plus_count') // 打胶成功次数
        table.bigint('glue_plus_length_total') // 打胶成功累计长度
        table.bigint('glue_punish_count') // 打胶失败次数
        table.bigint('glue_punish_length_total') // 打胶失败累计扣减长度

        // pk
        table.bigint('pk_win_count') // pk胜利次数
        table.bigint('pk_lose_count') // pk失败次数
        table.bigint('pk_plus_length_total') // pk胜利累计长度
        table.bigint('pk_punish_length_total') // pk失败累计扣减长度

        // lock
        table.bigint('lock_me_count') // 锁自己的次数
        table.bigint('lock_target_count') // 锁别人的次数
        table.bigint('lock_plus_count') // 锁成功次数
        table.bigint('lock_punish_count') // 锁失败次数
        table.bigint('lock_plus_length_total') // 锁成功累计长度
        table.bigint('lock_punish_length_total') // 锁失败累计扣减长度

      })
      .toSQL()
    // @ts-expect-error
    sql.push(createSqlWithBadge[0].sql)
    const insertSqlWithBadge = await ins('badge')
      .insert({
        qq: 123456789,
        badge_ids: '1,2,3',
        glue_me_count: 0,
        glue_target_count: 0,
        glue_plus_count: 0,
        glue_plus_length_total: 0,
        glue_punish_count: 0,
        glue_punish_length_total: 0,
        pk_win_count: 0,
        pk_lose_count: 0,
        pk_plus_length_total: 0,
        pk_punish_length_total: 0,
        lock_me_count: 0,
        lock_target_count: 0,
        lock_plus_count: 0,
        lock_punish_count: 0,
        lock_plus_length_total: 0,
        lock_punish_length_total: 0,
      })
      .toSQL()
    sql.push(insertSqlWithBadge.sql)
    const selectSqlWithBadge = await ins('badge')
      .select('*')
      .where('qq', 123456789)
      .toSQL()
    sql.push(selectSqlWithBadge.sql)
    // delete
    const deleteSqlWithBadge = await ins('badge')
      .where('qq', 123456789)
      .del()
      .toSQL()
    sql.push(deleteSqlWithBadge.sql)

    // farm
    sql.push('-- Farm Table --')
    const createSqlWithFarm = await ins.schema
      .createTableIfNotExists('farm', (table) => {
        table.bigint('qq').primary()
        table.string('farm_status')
        table.string('farm_latest_plant_time')
        table.integer('farm_need_time')
        table.integer('farm_count')
        table.float('farm_expect_get_length')
      })
      .toSQL()
    // @ts-expect-error
    sql.push(createSqlWithFarm[0].sql)
    const insertSqlWithFarm = await ins('farm')
      .insert({
        qq: 123456789,
        farm_status: 'status',
        farm_latest_plant_time: '2023-01-25 02:26:52',
        farm_need_time: 0,
        farm_count: 0,
        farm_expect_get_length: 0
      })
      .toSQL()
    sql.push(insertSqlWithFarm.sql)
    const selectSqlWithFarm = await ins('farm')
      .select('*')
      .where('qq', 123456789)
      .toSQL()
    sql.push(selectSqlWithFarm.sql)
    // delete
    const deleteSqlWithFarm = await ins('farm')
      .where('qq', 123456789)
      .del()
      .toSQL()
    sql.push(deleteSqlWithFarm.sql)

    // friends table
    sql.push('-- Friends Table --')
    const createSqlWithFriends = await ins.schema
      .createTableIfNotExists('friends', (table) => {
        table.bigint('qq').primary()
        table.string('friends_list') // 朋友列表
        table.integer('friends_share_count') // 被共享次数
        table.string('friends_cost_latest_time') // 上次付费日期
        table.float('friends_will_collect_length') // 准备收取的长度
        table.string('friends_collect_latest_time') // 上次收款时间
      })
      .toSQL()
    // @ts-expect-error
    sql.push(createSqlWithFriends[0].sql)
    const insertSqlWithFriends = await ins('friends')
      .insert({
        qq: 123456789,
        friends_list: '1,2,3',
        friends_share_count: 0,
        friends_cost_latest_time: '2023-01-25 02:26:52',
        friends_will_collect_length: 0,
        friends_collect_latest_time: '2023-01-25 02:26:52',
      })
      .toSQL()
    sql.push(insertSqlWithFriends.sql)
    const selectSqlWithFriends = await ins('friends')
      .select('*')
      .where('qq', 123456789)
      .toSQL()
    sql.push(selectSqlWithFriends.sql)
    // delete
    const deleteSqlWithFriends = await ins('friends')
      .where('qq', 123456789)
      .del()
      .toSQL()
    sql.push(deleteSqlWithFriends.sql)
    
    // write
    fs.writeFileSync(SQL_FILE, sql.join(';\n') + ';\n', 'utf-8')
  } catch (e) {
    console.error(e)
  } finally {
    await ins.destroy()
  }
}

run()
