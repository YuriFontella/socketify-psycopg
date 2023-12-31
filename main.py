from socketify import App

from db import Database

db = Database().conn

app = App()

def get(res, req):
  records = db.execute("select name from users limit 10000").fetchall()
  res.send(records)

async def post(res, req):
  data = await res.get_json()

  try:

    query = """
      insert into groups (name, total, saved) 
      values 
        (
          %(name)s, 
          %(total)s, 
          %(saved)s
        ) on conflict (name) do 
      update 
      set 
        (total, saved) = (excluded.total, excluded.saved) returning id
    """

    record = db.execute(query, data).fetchone()
    print(record['id'])

  except RuntimeError: 
    raise RuntimeError(db.DatabaseError)

  else:
    db.commit()

    res.end(True)

  finally:
    print('Transação encerrada')


async def put(res, req):

  try:
    query = "update groups set name = %(name)s where id = %(id)s"

    params = await res.get_json()
    params.update({ id: req.get_parameter(0) })

    db.execute(query, params)

  except RuntimeError: 
    raise(db.DatabaseError)
  
  else:
    db.commit()

    res.end(True)


def delete(res, req):
  db.execute("delete from groups where id = (%s)", (req.get_parameter(0),))
  db.commit()

  res.end(True)

def on_error(error, res, req):
  print(str(error))

  if res != None:
    res.write_status(500).end('Algo deu errado')

app.get("/", get)
app.post("/", post)
app.put("/:id", put)
app.delete("/:id", delete)

app.set_error_handler(on_error)

app.listen(3000)
app.run()
