public IEnumerable<Entity> GetValue(int Val)
{
    try
    {
        using (var sqCon = new SqlConnection(_connectionString))
        {
            var ret = new List<vwValLoadServingEntity>();
            sqCon.Open();
            using (var sqCmd = sqCon.CreateCommand())
            {
                sqCmd.CommandType = CommandType.Text;
                sqCmd.CommandText = "SELECT * FROM Database.Table WHERE Id = @Val";
                sqCmd.Parameters.AddWithValue("@Val", Val);
                using (var sqReader = sqCmd.ExecuteReader())
                {
                    while (sqReader.Read())
                    {
                        ret.Add(SqlDalUtils.ReadColumns<vwVal>(sqReader));
                    }
                    return ret;
                }
            } // end using SqlCommand
        } // end using SqlConnection
    }
    catch (Exception e)
    {
        _log.Error("An exception occured in GetValue", e);
        throw new Exception("An exception occured in GetValue", e);
    }
}